package ideas

import (
	"context"

	"silan-backend/internal/ent"
	"silan-backend/internal/ent/idea"
	"silan-backend/internal/svc"
	"silan-backend/internal/types"

	"github.com/zeromicro/go-zero/core/logx"
)

type GetIdeaCategoriesLogic struct {
	logx.Logger
	ctx    context.Context
	svcCtx *svc.ServiceContext
}

// Get idea categories
func NewGetIdeaCategoriesLogic(ctx context.Context, svcCtx *svc.ServiceContext) *GetIdeaCategoriesLogic {
	return &GetIdeaCategoriesLogic{
		Logger: logx.WithContext(ctx),
		ctx:    ctx,
		svcCtx: svcCtx,
	}
}

func (l *GetIdeaCategoriesLogic) GetIdeaCategories(req *types.IdeaCategoriesRequest) (resp []string, err error) {
	// Get distinct categories using entgo
	ideas, err := l.svcCtx.DB.Idea.Query().
		Where(idea.CategoryNEQ("")).
		Where(idea.CategoryNotNil()).
		Order(ent.Asc(idea.FieldCategory)).
		All(l.ctx)
	if err != nil {
		return nil, err
	}

	// Extract unique categories
	categorySet := make(map[string]bool)
	var categories []string
	for _, ideaItem := range ideas {
		if ideaItem.Category != "" && !categorySet[ideaItem.Category] {
			categorySet[ideaItem.Category] = true
			categories = append(categories, ideaItem.Category)
		}
	}

	if categories == nil {
		categories = []string{}
	}
	return categories, nil
}
