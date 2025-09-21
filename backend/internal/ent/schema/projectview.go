package schema

import (
	"time"

	"entgo.io/ent"
	"entgo.io/ent/dialect/entsql"
	"entgo.io/ent/schema"
	"entgo.io/ent/schema/edge"
	"entgo.io/ent/schema/field"
	"entgo.io/ent/schema/index"
	"github.com/google/uuid"
)

// ProjectView holds the schema definition for the ProjectView entity.
type ProjectView struct {
	ent.Schema
}

// Annotations for the ProjectView schema.
func (ProjectView) Annotations() []schema.Annotation {
	return []schema.Annotation{
		entsql.Annotation{Table: "project_views"},
	}
}

// Fields of the ProjectView.
func (ProjectView) Fields() []ent.Field {
	return []ent.Field{
		field.UUID("id", uuid.UUID{}).
			Default(uuid.New).
			StorageKey("id"),
		field.UUID("project_id", uuid.UUID{}).
			StorageKey("project_id").
			Comment("Project ID that was viewed"),
		field.String("user_identity_id").
			Optional().
			Comment("ID of the authenticated user who viewed"),
		field.String("fingerprint").
			Optional().
			Comment("Browser fingerprint for anonymous views"),
		field.String("ip_address").
			Optional().
			MaxLen(45).
			Comment("IP address of the user who viewed"),
		field.String("user_agent").
			Optional().
			Comment("User agent string"),
		field.String("referrer").
			Optional().
			Comment("Referrer URL"),
		field.Int("session_duration").
			Optional().
			Default(0).
			Comment("Duration spent viewing in seconds"),
		field.Time("created_at").
			Default(time.Now).
			Immutable(),
		field.Time("updated_at").
			Default(time.Now).
			UpdateDefault(time.Now),
	}
}

// Edges of the ProjectView.
func (ProjectView) Edges() []ent.Edge {
	return []ent.Edge{
		edge.From("project", Project.Type).
			Ref("views").
			Field("project_id").
			Required().
			Unique(),
		edge.To("user_identity", UserIdentity.Type).
			Field("user_identity_id").
			Unique(),
	}
}

// Indexes of the ProjectView.
func (ProjectView) Indexes() []ent.Index {
	return []ent.Index{
		// Performance indexes
		index.Fields("project_id"),
		index.Fields("user_identity_id"),
		index.Fields("fingerprint"),
		index.Fields("ip_address"),
		index.Fields("created_at"),
		// Composite index for analytics queries
		index.Fields("project_id", "created_at"),
	}
}