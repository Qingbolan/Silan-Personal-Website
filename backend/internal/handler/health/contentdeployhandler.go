package health

import (
	"errors"
	"fmt"
	"net/http"
	"strings"

	"silan-backend/internal/contentdeploy"
	"silan-backend/internal/svc"

	"github.com/zeromicro/go-zero/rest/httpx"
)

const contentDeployMediaType = "application/vnd.silan.content-deploy+tar+gzip"
const contentSourceMediaType = "application/vnd.silan.content-source+tar"

func ContentDeployHandler(svcCtx *svc.ServiceContext) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if !strings.HasPrefix(r.Header.Get("Content-Type"), contentDeployMediaType) {
			httpx.ErrorCtx(r.Context(), w, errors.New("content deploy requires a gzip bundle"))
			return
		}
		r.Body = http.MaxBytesReader(w, r.Body, svcCtx.Config.ContentDeployMaxBundleBytes())
		result, err := svcCtx.ContentDeploy.Deploy(r.Context(), r.Body)
		if err != nil {
			var mediaRequired *contentdeploy.MediaRequiredError
			if errors.As(err, &mediaRequired) {
				httpx.WriteJson(w, http.StatusConflict, contentdeploy.PlanResult{
					UploadPaths: mediaRequired.UploadPaths,
				})
				return
			}
			var tooLarge *http.MaxBytesError
			if errors.As(err, &tooLarge) {
				http.Error(w, "deployment bundle is too large", http.StatusRequestEntityTooLarge)
				return
			}
			http.Error(w, fmt.Sprintf("content deployment failed: %v", err), http.StatusUnprocessableEntity)
			return
		}
		httpx.OkJsonCtx(r.Context(), w, result)
	}
}

func ContentSourceHandler(svcCtx *svc.ServiceContext) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		snapshot, err := svcCtx.ContentDeploy.CurrentSource(r.Context())
		if err != nil {
			http.Error(w, fmt.Sprintf("content source recovery failed: %v", err), http.StatusNotFound)
			return
		}
		w.Header().Set("Content-Type", contentSourceMediaType)
		w.Header().Set("Content-Disposition", "attachment; filename=content-source.tar")
		w.Header().Set("X-Silan-Content-Commit", snapshot.ContentCommit)
		w.Header().Set("X-Silan-Source-SHA256", snapshot.SourceSHA)
		w.Header().Set("Cache-Control", "private, no-store")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write(snapshot.Bytes)
	}
}

func ContentRollbackHandler(svcCtx *svc.ServiceContext) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		result, err := svcCtx.ContentDeploy.Rollback(r.Context())
		if err != nil {
			http.Error(w, fmt.Sprintf("content rollback failed: %v", err), http.StatusUnprocessableEntity)
			return
		}
		httpx.OkJsonCtx(r.Context(), w, result)
	}
}
