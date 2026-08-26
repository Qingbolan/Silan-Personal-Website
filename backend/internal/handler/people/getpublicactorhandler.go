package people

import (
	"errors"
	"net/http"

	"silan-backend/internal/logic/people"
	"silan-backend/internal/svc"
	"silan-backend/internal/types"

	"github.com/zeromicro/go-zero/rest/httpx"
)

func GetPublicActorHandler(svcCtx *svc.ServiceContext) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var req types.PublicActorRequest
		if err := httpx.Parse(r, &req); err != nil {
			httpx.ErrorCtx(r.Context(), w, err)
			return
		}

		logic := people.NewGetPublicActorLogic(r.Context(), svcCtx)
		resp, err := logic.GetPublicActor(&req)
		if errors.Is(err, people.ErrPublicActorNotFound) {
			httpx.WriteJson(w, http.StatusNotFound, map[string]string{"message": "public profile not found"})
			return
		}
		if err != nil {
			httpx.ErrorCtx(r.Context(), w, err)
			return
		}
		httpx.OkJsonCtx(r.Context(), w, resp)
	}
}
