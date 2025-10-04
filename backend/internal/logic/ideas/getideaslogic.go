package ideas

import (
	"context"
	"fmt"
	"math"
	"strings"

	"silan-backend/internal/ent"
	"silan-backend/internal/ent/idea"
	"silan-backend/internal/ent/ideadetail"
	"silan-backend/internal/svc"
	"silan-backend/internal/types"

	"github.com/zeromicro/go-zero/core/logx"
)

type GetIdeasLogic struct {
	logx.Logger
	ctx    context.Context
	svcCtx *svc.ServiceContext
}

// Get ideas list with pagination and filtering
func NewGetIdeasLogic(ctx context.Context, svcCtx *svc.ServiceContext) *GetIdeasLogic {
	return &GetIdeasLogic{
		Logger: logx.WithContext(ctx),
		ctx:    ctx,
		svcCtx: svcCtx,
	}
}

func (l *GetIdeasLogic) GetIdeas(req *types.IdeaListRequest) (resp *types.IdeaListResponse, err error) {
	query := l.svcCtx.DB.Idea.Query().
		Where(idea.IsPublic(true)).
		WithUser()

	// Apply filters
	if req.Status != "" {
		query = query.Where(idea.StatusEQ(idea.Status(req.Status)))
	}

	if req.Collaboration {
		query = query.Where(idea.HasDetailsWith(ideadetail.CollaborationNeeded(true)))
	}

	if req.Funding != "" {
		if req.Funding == "required" {
			query = query.Where(idea.HasDetailsWith(ideadetail.FundingRequired(true)))
		} else if req.Funding == "not_required" {
			query = query.Where(idea.HasDetailsWith(ideadetail.FundingRequired(false)))
		}
	}

	if req.Search != "" {
		query = query.Where(idea.Or(
			idea.TitleContains(req.Search),
			idea.DescriptionContains(req.Search),
			idea.AbstractContains(req.Search),
		))
	}

	// Get total count
	total, err := query.Count(l.ctx)
	if err != nil {
		return nil, err
	}

	// Apply pagination
	offset := (req.Page - 1) * req.Size
	ideas, err := query.
		WithTags().
		WithDetails().
		Order(ent.Desc(idea.FieldUpdatedAt)).
		Limit(req.Size).
		Offset(offset).
		All(l.ctx)
	if err != nil {
		return nil, err
	}

	// Category now comes directly from Ent field after schema sync

	var result []types.IdeaData
	for _, ideaEntity := range ideas {
		// Handle non-nullable fields
		abstract := ideaEntity.Abstract
		description := ideaEntity.Description

		// Get detail fields from IdeaDetail edge
		var progress, results, references, requiredResources string
		var collaborationNeeded bool
		var estimatedDuration string

		if ideaEntity.Edges.Details != nil {
			detail := ideaEntity.Edges.Details
			progress = detail.Progress
			results = detail.Results
			references = detail.References
			requiredResources = detail.RequiredResources
			collaborationNeeded = detail.CollaborationNeeded

			if detail.EstimatedDurationMonths > 0 {
				estimatedDuration = fmt.Sprintf("%d months", detail.EstimatedDurationMonths)
			}
		}

		// Tags from M2M edge (IdeaTag)
		tags := []string{}
		if len(ideaEntity.Edges.Tags) > 0 {
			for _, t := range ideaEntity.Edges.Tags {
				if t.Name != "" {
					tags = append(tags, t.Name)
				}
			}
		}
		category := ideaEntity.Category

		// Initialize missing variables
		var codeRepository string
		var demoURL string
		var techStack []string
		var collaborators []types.Collaborator
		var feedbackRequested []types.FeedbackType
		var publications []types.IdeaPublicationRef
		var conferences []string
		var keywords []string

		result = append(result, types.IdeaData{
			ID:                   ideaEntity.ID.String(),
			Title:                ideaEntity.Title,
			Description:          description,
			Category:             category,
			Tags:                 tags,
			Status:               strings.ToLower(string(ideaEntity.Status)),
			CreatedAt:            ideaEntity.CreatedAt.Format("2006-01-02T15:04:05Z"),
			LastUpdated:          ideaEntity.UpdatedAt.Format("2006-01-02T15:04:05Z"),
			Abstract:             abstract,
			AbstractZh:           abstract,
			Progress:             progress,
			ProgressZh:           progress,
			Results:              results,
			ResultsZh:            results,
			Reference:            references,
			Reference_Zh:         references,
			TechStack:            techStack,
			CodeRepository:       codeRepository,
			DemoURL:              demoURL,
			Collaborators:        collaborators,
			OpenForCollaboration: collaborationNeeded,
			FeedbackRequested:    feedbackRequested,
			Publications:         publications,
			Conferences:          conferences,
			ResearchField:        category,
			Keywords:             keywords,
			EstimatedDuration:    estimatedDuration,
			FundingStatus:        requiredResources,
		})
	}

	// Handle empty result
	if result == nil {
		result = []types.IdeaData{}
	}

	totalPages := int(math.Ceil(float64(total) / float64(req.Size)))

	return &types.IdeaListResponse{
		Ideas:      result,
		Total:      int64(total),
		Page:       req.Page,
		Size:       req.Size,
		TotalPages: totalPages,
	}, nil
}
