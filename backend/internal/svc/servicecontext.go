package svc

import (
	"log"

	"silan-backend/internal/config"
	"silan-backend/internal/ent"
	"silan-backend/internal/middleware"

	"github.com/zeromicro/go-zero/rest"

	_ "github.com/go-sql-driver/mysql"
	_ "github.com/lib/pq"
	_ "github.com/mattn/go-sqlite3"
)

type ServiceContext struct {
	Config config.Config
	Cors   rest.Middleware
	DB     *ent.Client
}

func NewServiceContext(c config.Config) *ServiceContext {
	client, err := ent.Open(c.Database.Driver, c.Database.Source)
	if err != nil {
		log.Fatalf("failed opening connection to database: %v", err)
	}

	return &ServiceContext{
		Config: c,
		Cors:   middleware.NewCorsMiddleware().Handle,
		DB:     client,
	}
}
