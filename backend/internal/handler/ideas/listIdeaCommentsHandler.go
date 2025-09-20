package ideas

import (
	"net/http"

	"github.com/zeromicro/go-zero/rest/httpx"
	ideaslogic "silan-backend/internal/logic/ideas"
	"silan-backend/internal/svc"
	"silan-backend/internal/types"
	"silan-backend/internal/utils"
)

// List comments for an idea
func ListIdeaCommentsHandler(svcCtx *svc.ServiceContext) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var req types.IdeaCommentListRequest
		if err := httpx.Parse(r, &req); err != nil {
			httpx.ErrorCtx(r.Context(), w, err)
			return
		}

		l := ideaslogic.NewListIdeaCommentsLogic(r.Context(), svcCtx)
		clientIP := utils.GetClientIP(r)
		userAgent := utils.GetUserAgent(r)
		fingerprint := r.URL.Query().Get("fingerprint")
		userIdentityID := r.URL.Query().Get("user_identity_id")

		resp, err := l.ListComments(&req, clientIP, userAgent, fingerprint, userIdentityID)
		if err != nil {
			httpx.ErrorCtx(r.Context(), w, err)
			return
		}
		httpx.OkJsonCtx(r.Context(), w, resp)
	}
}

