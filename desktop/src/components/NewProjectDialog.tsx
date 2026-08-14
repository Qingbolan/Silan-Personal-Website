import React from 'react';
import { AlertCircle, FolderPlus } from 'lucide-react';
import { slugPreview } from '../lib/format';
import { Button } from './ds/Button';
import {
  Dialog,
  DialogActions,
  DialogCard,
  DialogDescription,
  DialogTitle,
} from './ds/Dialog';
import { Input } from './ds/Input';

type NewProjectDialogProps = {
  title: string;
  onTitleChange: (value: string) => void;
  submitting: boolean;
  error: string | null;
  inputRef: React.RefObject<HTMLInputElement>;
  onCancel: () => void;
  onSubmit: () => void;
  onKeyDown: (event: React.KeyboardEvent<HTMLInputElement>) => void;
};

export function NewProjectDialog({
  title,
  onTitleChange,
  submitting,
  error,
  inputRef,
  onCancel,
  onSubmit,
  onKeyDown,
}: NewProjectDialogProps) {
  return (
    <Dialog open onClose={onCancel}>
      <DialogCard className="new-project-card" aria-labelledby="new-project-title">
        <div className="new-project-badge">
          <FolderPlus size={17} />
        </div>
        <DialogTitle id="new-project-title">New project</DialogTitle>
        <DialogDescription>
          Creates a real content/project source with an overview Part, then opens it for editing.
        </DialogDescription>
        <label className="new-project-field">
          <Input
            ref={inputRef}
            type="text"
            value={title}
            onChange={(event) => onTitleChange(event.target.value)}
            onKeyDown={onKeyDown}
            disabled={submitting}
            placeholder="Project title"
            aria-label="Project title"
            data-autofocus
          />
          <span className="new-project-slug">
            content/resources/projects/{title.trim() ? slugPreview(title) : '...'}
          </span>
        </label>
        {error && (
          <div className="dialog-error" role="alert">
            <AlertCircle size={14} />
            <span>{error}</span>
          </div>
        )}
        <DialogActions>
          <Button type="button" variant="secondary" size="sm" disabled={submitting} onClick={onCancel}>
            Cancel
          </Button>
          <Button
            type="button"
            variant="primary"
            size="sm"
            loading={submitting}
            disabled={!title.trim() || submitting}
            onClick={onSubmit}
          >
            {!submitting && <FolderPlus size={15} />}
            {submitting ? 'Creating' : 'Create project'}
          </Button>
        </DialogActions>
      </DialogCard>
    </Dialog>
  );
}
