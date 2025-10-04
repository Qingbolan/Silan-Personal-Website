package ideas

import (
	"context"
	"fmt"
	"math"
	"strings"

	"silan-backend/internal/ent"
	"silan-backend/internal/ent/idea"
	"silan-backend/internal/svc"
	"silan-backend/internal/types"

	"github.com/zeromicro/go-zero/core/logx"
)

type SearchIdeasLogic struct {
	logx.Logger
	ctx    context.Context
	svcCtx *svc.ServiceContext
}

// Search ideas with filters
func NewSearchIdeasLogic(ctx context.Context, svcCtx *svc.ServiceContext) *SearchIdeasLogic {
	return &SearchIdeasLogic{
		Logger: logx.WithContext(ctx),
		ctx:    ctx,
		svcCtx: svcCtx,
	}
}

func (l *SearchIdeasLogic) SearchIdeas(req *types.IdeaSearchRequest) (resp *types.IdeaListResponse, err error) {
	query := l.svcCtx.DB.Idea.Query().
		Where(idea.IsPublic(true)).
		WithUser()

	// Apply search query if provided
	if req.Query != "" {
		query = query.Where(idea.Or(
			idea.TitleContains(req.Query),
			idea.DescriptionContains(req.Query),
			idea.AbstractContains(req.Query),
		))
	}

	// Apply status filter
	if req.Status != "" {
		query = query.Where(idea.StatusEQ(idea.Status(req.Status)))
	}

	// Apply category filter
	// Note: This would work if categories were stored as a field in the idea table
	// For now, we'll skip this filter since the schema doesn't have a category field
	if req.Category != "" {
		// This would be implemented when the schema is updated:
		// query = query.Where(idea.CategoryContains(req.Category))
	}

	// Apply tags filter
	// Note: This would work if tags were stored as a field or relationship
	// For now, we'll skip this filter since the schema doesn't have tags
	if req.Tags != "" {
		// This would be implemented when the schema is updated:
		// tagList := strings.Split(req.Tags, ",")
		// for _, tag := range tagList {
		//     query = query.Where(idea.HasTagsWith(ideatag.NameContains(strings.TrimSpace(tag))))
		// }
	}

	// Get total count
	total, err := query.Count(l.ctx)
	if err != nil {
		return nil, err
	}

	// Apply pagination
	offset := (req.Page - 1) * req.Size
	ideas, err := query.
		WithDetails().
		WithTags().
		Order(ent.Desc(idea.FieldUpdatedAt)).
		Limit(req.Size).
		Offset(offset).
		All(l.ctx)
	if err != nil {
		return nil, err
	}

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

		collaborators := []types.Collaborator{}

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
			Collaborators:        collaborators,
			OpenForCollaboration: collaborationNeeded,
			FeedbackRequested:    feedbackRequested,
			Publications:         publications,
			Conferences:          conferences,
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
