import { Button } from './ds/Button';
import {
  Dialog,
  DialogActions,
  DialogCard,
  DialogDescription,
  DialogTitle,
} from './ds/Dialog';

type RefreshConfirmDialogProps = {
  dirtyCount: number;
  onCancel: () => void;
  onConfirm: () => void;
};

export function RefreshConfirmDialog({ dirtyCount, onCancel, onConfirm }: RefreshConfirmDialogProps) {
  return (
    <Dialog open onClose={onCancel}>
      <DialogCard role="alertdialog" aria-labelledby="refresh-confirm-title">
        <DialogTitle id="refresh-confirm-title">
          Discard {dirtyCount} unsaved change{dirtyCount > 1 ? 's' : ''}?
        </DialogTitle>
        <DialogDescription>
          Refreshing reloads the source tree and discards Markdown edits that haven&apos;t been saved yet.
        </DialogDescription>
        <DialogActions>
          <Button type="button" variant="secondary" size="sm" onClick={onCancel}>Cancel</Button>
          <Button type="button" variant="destructive" size="sm" onClick={onConfirm}>Discard and refresh</Button>
        </DialogActions>
      </DialogCard>
    </Dialog>
  );
}
