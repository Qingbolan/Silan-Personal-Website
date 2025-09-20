package ideas

import (
	"context"

	"silan-backend/internal/ent/ideatag"
	"silan-backend/internal/svc"
	"silan-backend/internal/types"

	"github.com/zeromicro/go-zero/core/logx"
)

type GetIdeaTagsLogic struct {
	logx.Logger
	ctx    context.Context
	svcCtx *svc.ServiceContext
}

// Get idea tags
func NewGetIdeaTagsLogic(ctx context.Context, svcCtx *svc.ServiceContext) *GetIdeaTagsLogic {
	return &GetIdeaTagsLogic{
		Logger: logx.WithContext(ctx),
		ctx:    ctx,
		svcCtx: svcCtx,
	}
}

func (l *GetIdeaTagsLogic) GetIdeaTags(req *types.IdeaTagsRequest) (resp []string, err error) {
	// Query distinct tag names ordered by name from idea_tags
	tags, err := l.svcCtx.DB.IdeaTag.Query().
		Order(ideatag.ByName()).
		All(l.ctx)
	if err != nil {
		return nil, err
	}
	names := make([]string, 0, len(tags))
	for _, t := range tags {
		if t.Name != "" {
			names = append(names, t.Name)
		}
	}
	return names, nil
}
