package ideas

import (
	"context"
	"fmt"
	"strings"

	"silan-backend/internal/ent/idea"
	"silan-backend/internal/svc"
	"silan-backend/internal/types"

	"github.com/google/uuid"
	"github.com/zeromicro/go-zero/core/logx"
)

type GetIdeaLogic struct {
	logx.Logger
	ctx    context.Context
	svcCtx *svc.ServiceContext
}

// Get single idea by ID
func NewGetIdeaLogic(ctx context.Context, svcCtx *svc.ServiceContext) *GetIdeaLogic {
	return &GetIdeaLogic{
		Logger: logx.WithContext(ctx),
		ctx:    ctx,
		svcCtx: svcCtx,
	}
}

func (l *GetIdeaLogic) GetIdea(req *types.IdeaRequest) (resp *types.IdeaData, err error) {
	// Parse UUID
	ideaID, err := uuid.Parse(req.ID)
	if err != nil {
		return nil, fmt.Errorf("invalid idea ID: %w", err)
	}

	// Query the idea
	ideaEntity, err := l.svcCtx.DB.Idea.Query().
		Where(idea.ID(ideaID)).
		WithUser().
		WithTags().
		First(l.ctx)
	if err != nil {
		return nil, err
	}

	// Convert to response format
	// Note: Author field not used in IdeaData response

	// Handle non-nullable fields
	abstract := ideaEntity.Abstract
	motivation := ideaEntity.Motivation
	methodology := ideaEntity.Methodology
	expectedOutcome := ideaEntity.ExpectedOutcome
	requiredResources := ideaEntity.RequiredResources

	var estimatedDuration string
	if ideaEntity.EstimatedDurationMonths > 0 {
		estimatedDuration = fmt.Sprintf("%d months", ideaEntity.EstimatedDurationMonths)
	}

	// Note: EstimatedBudget field not used in IdeaData response

	// Tags from M2M edge (IdeaTag)
	var tags []string
	if ideaEntity.Edges.Tags != nil && len(ideaEntity.Edges.Tags) > 0 {
		for _, t := range ideaEntity.Edges.Tags {
			if t.Name != "" {
				tags = append(tags, t.Name)
			}
		}
	} else {
		tags = []string{}
	}
	// Category: now directly from Ent field
	category := ideaEntity.Category

	// Create empty slices for complex fields
	var futureDirections []string
	if len(futureDirections) == 0 {
		futureDirections = []string{}
	}

	var techStack []string
	if len(techStack) == 0 {
		techStack = []string{}
	}

	var keywords []string
	if len(keywords) == 0 {
		keywords = []string{}
	}

	var keyFindings []string
	if len(keyFindings) == 0 {
		keyFindings = []string{}
	}

	var limitations []string
	if len(limitations) == 0 {
		limitations = []string{}
	}

	var collaborators []types.Collaborator
	if len(collaborators) == 0 {
		collaborators = []types.Collaborator{}
	}

	var experiments []types.Experiment
	if len(experiments) == 0 {
		experiments = []types.Experiment{}
	}

	var relatedWorks []types.Reference
	if len(relatedWorks) == 0 {
		relatedWorks = []types.Reference{}
	}

	var citations []types.Reference
	if len(citations) == 0 {
		citations = []types.Reference{}
	}

	var feedbackRequested []types.FeedbackType
	if len(feedbackRequested) == 0 {
		feedbackRequested = []types.FeedbackType{}
	}

	var publications []types.IdeaPublicationRef
	if len(publications) == 0 {
		publications = []types.IdeaPublicationRef{}
	}

	var conferences []string
	if len(conferences) == 0 {
		conferences = []string{}
	}

	return &types.IdeaData{
		ID:                   ideaEntity.ID.String(),
		Title:                ideaEntity.Title,
		Description:          abstract,
		Category:             category,
		Tags:                 tags,
		Status:               strings.ToLower(string(ideaEntity.Status)),
		CreatedAt:            ideaEntity.CreatedAt.Format("2006-01-02T15:04:05Z"),
		LastUpdated:          ideaEntity.UpdatedAt.Format("2006-01-02T15:04:05Z"),
		Abstract:             abstract,
		Motivation:           motivation,
		Methodology:          methodology,
		Experiments:          experiments,
		PreliminaryResults:   expectedOutcome,
		RelatedWorks:         relatedWorks,
		Citations:            citations,
		FutureDirections:     futureDirections,
		TechStack:            techStack,
		Collaborators:        collaborators,
		OpenForCollaboration: ideaEntity.CollaborationNeeded,
		FeedbackRequested:    feedbackRequested,
		Publications:         publications,
		Conferences:          conferences,
		KeyFindings:          keyFindings,
		Limitations:          limitations,
		Difficulty:           strings.ToLower(string(ideaEntity.Priority)),
		Keywords:             keywords,
		EstimatedDuration:    estimatedDuration,
		FundingStatus:        requiredResources,
	}, nil
}
