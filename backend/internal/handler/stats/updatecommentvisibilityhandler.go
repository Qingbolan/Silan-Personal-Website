package stats

import (
	"net/http"

	statslogic "silan-backend/internal/logic/stats"
	"silan-backend/internal/svc"
	"silan-backend/internal/types"

	"github.com/zeromicro/go-zero/rest/httpx"
)

// UpdateCommentVisibilityHandler exposes the sole operator mutation supported
// by the interaction workbench: publishing or hiding an existing comment.
func UpdateCommentVisibilityHandler(svcCtx *svc.ServiceContext) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var req types.UpdateCommentVisibilityRequest
		if err := httpx.Parse(r, &req); err != nil {
			httpx.ErrorCtx(r.Context(), w, err)
			return
		}
		resp, err := statslogic.NewStatsLogic(r.Context(), svcCtx).UpdateCommentVisibility(&req)
		if err != nil {
			httpx.ErrorCtx(r.Context(), w, err)
			return
		}
		httpx.OkJsonCtx(r.Context(), w, resp)
	}
}
