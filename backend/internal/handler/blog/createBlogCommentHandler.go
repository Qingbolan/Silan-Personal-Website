package blog

import (
	"net/http"

	"github.com/zeromicro/go-zero/rest/httpx"
	"silan-backend/internal/logic/blog"
	"silan-backend/internal/svc"
	"silan-backend/internal/types"
)

// Create a comment for a blog post
func CreateBlogCommentHandler(svcCtx *svc.ServiceContext) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var req types.CreateBlogCommentRequest
		if err := httpx.Parse(r, &req); err != nil {
			httpx.ErrorCtx(r.Context(), w, err)
			return
		}

		l := blog.NewCreateBlogCommentLogic(r.Context(), svcCtx)
		resp, err := l.CreateBlogComment(&req)
		if err != nil {
			httpx.ErrorCtx(r.Context(), w, err)
		} else {
			httpx.OkJsonCtx(r.Context(), w, resp)
		}
	}
}
