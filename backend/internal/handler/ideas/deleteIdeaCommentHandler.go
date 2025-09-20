package ideas

import (
	"net/http"

	"github.com/zeromicro/go-zero/rest/httpx"
	ideaslogic "silan-backend/internal/logic/ideas"
	"silan-backend/internal/svc"
	"silan-backend/internal/types"
)

// Delete a comment for idea (authorization required)
func DeleteIdeaCommentHandler(svcCtx *svc.ServiceContext) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var req types.DeleteIdeaCommentRequest
		if err := httpx.Parse(r, &req); err != nil {
			httpx.ErrorCtx(r.Context(), w, err)
			return
		}
		l := ideaslogic.NewDeleteIdeaCommentLogic(r.Context(), svcCtx)
		if err := l.DeleteComment(&req); err != nil {
			httpx.ErrorCtx(r.Context(), w, err)
			return
		}
		httpx.OkJsonCtx(r.Context(), w, map[string]any{"ok": true})
	}
}

