package projects

import (
	"context"
	"fmt"
	"time"

	"silan-backend/internal/ent/project"
	"silan-backend/internal/ent/projectdetail"
	"silan-backend/internal/ent/projecttechnology"
	"silan-backend/internal/svc"
	"silan-backend/internal/types"

	"github.com/zeromicro/go-zero/core/logx"
)

type SearchProjectDetailsLogic struct {
	logx.Logger
	ctx    context.Context
	svcCtx *svc.ServiceContext
}

// Search project details with filters
func NewSearchProjectDetailsLogic(ctx context.Context, svcCtx *svc.ServiceContext) *SearchProjectDetailsLogic {
	return &SearchProjectDetailsLogic{
		Logger: logx.WithContext(ctx),
		ctx:    ctx,
		svcCtx: svcCtx,
	}
}

func (l *SearchProjectDetailsLogic) SearchProjectDetails(req *types.ProjectSearchRequest) (resp []types.ProjectDetail, err error) {
	// Build the query with filters - search through project details with project join
	// Only include public projects
	query := l.svcCtx.DB.ProjectDetail.Query().
		WithProject().
		Where(projectdetail.HasProjectWith(project.IsPublic(true)))
	
	// Apply filters through project relationship if provided
	if req.Query != "" {
		query = query.Where(
			projectdetail.Or(
				projectdetail.ReleaseNotesContains(req.Query),
				projectdetail.QuickStartContains(req.Query),
				projectdetail.DependenciesContains(req.Query),
				projectdetail.LicenseTextContains(req.Query),
				projectdetail.VersionContains(req.Query),
				projectdetail.HasProjectWith(
					project.Or(
						project.TitleContains(req.Query),
						project.DescriptionContains(req.Query),
					),
				),
			),
		)
	}
	
	if req.Tags != "" {
		query = query.Where(
			projectdetail.HasProjectWith(
				project.HasTechnologiesWith(
					projecttechnology.TechnologyNameContains(req.Tags),
				),
			),
		)
	}
	
	if req.Year > 0 {
		query = query.Where(
			projectdetail.HasProjectWith(
				project.CreatedAtGTE(time.Date(req.Year, 1, 1, 0, 0, 0, 0, time.UTC)),
				project.CreatedAtLTE(time.Date(req.Year, 12, 31, 23, 59, 59, 999999999, time.UTC)),
			),
		)
	}
	
	// Execute the query
	projectDetails, err := query.All(l.ctx)
	if err != nil {
		return nil, err
	}
	
	// Convert to response format
	result := make([]types.ProjectDetail, 0, len(projectDetails))
	for _, pd := range projectDetails {
		// Get timeline data from the related project
		timeline := types.ProjectTimeline{
			Start:    "",
			End:      "",
			Duration: "",
		}
		
		// Get metrics data from the related project
		metrics := types.ProjectMetrics{
			LinesOfCode: 0,
			Commits:     0,
			Stars:       0,
			Downloads:   0,
		}
		
		// If project is loaded, get additional data
		if pd.Edges.Project != nil {
			proj := pd.Edges.Project
			if !proj.StartDate.IsZero() {
				timeline.Start = proj.StartDate.Format("2006-01-02")
			}
			if !proj.EndDate.IsZero() {
				timeline.End = proj.EndDate.Format("2006-01-02")
			}

			// Calculate duration if both dates are available
			if !proj.StartDate.IsZero() && !proj.EndDate.IsZero() {
				duration := proj.EndDate.Sub(proj.StartDate)
				days := int(duration.Hours() / 24)
				if days > 0 {
					timeline.Duration = fmt.Sprintf("%d days", days)
				}
			}

			metrics.Stars = proj.LikeCount
		}
		
		// Get values from project detail entity (these are strings, not pointers)
		releaseNotes := pd.ReleaseNotes
		quickStart := pd.QuickStart
		dependencies := pd.Dependencies
		license := pd.License
		licenseText := pd.LicenseText
		version := pd.Version

		// Get detailed description from related project if available
		var detailedDescription string
		if pd.Edges.Project != nil {
			detailedDescription = pd.Edges.Project.Description
		}

		result = append(result, types.ProjectDetail{
			ID:                  pd.ID.String(),
			ProjectID:           pd.ProjectID.String(),
			DetailedDescription: detailedDescription,
			Release:             releaseNotes,
			QuickStart:          quickStart,
			Dependance:          dependencies,
			LicenseText:         licenseText,
			License:             license,
			Version:             version,
			Timeline:            timeline,
			Metrics:             metrics,
			RelatedBlogs:        []types.ProjectBlogRef{},
			CreatedAt:           pd.CreatedAt.Format("2006-01-02 15:04:05"),
			UpdatedAt:           pd.UpdatedAt.Format("2006-01-02 15:04:05"),
		})
	}
	
	return result, nil
}
