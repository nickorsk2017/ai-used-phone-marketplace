"use client";

import { AlertDialog, Button } from "@heroui/react";
import { useMemo, useState } from "react";
import { useMyListingsStore } from "@/stores/myListingsStore";

interface DeletePhoneDialogProps {
  phone: Entity.Phone | null;
  onClose: () => void;
}

/** Delete Phone Flow: docs/features/MY_LISTING.md#delete-phone-flow. */
export function DeletePhoneDialog({ phone, onClose }: DeletePhoneDialogProps) {
  const remove = useMyListingsStore((state) => state.remove);
  const [isDeleting, setIsDeleting] = useState(false);
  const [hasError, setHasError] = useState(false);

  const close = () => {
    setHasError(false);
    onClose();
  };

  const confirm = async () => {
    if (!phone) {
      return;
    }
    setIsDeleting(true);
    setHasError(false);
    const response = await remove(phone.id);
    setIsDeleting(false);
    if (response.success) {
      close();
    } else {
      setHasError(true);
    }
  };

  const deleteErrorJSX = useMemo(() => {
    if (!hasError) {
      return null;
    }
    return (
      <p role="alert" className="text-sm text-danger">
        Could not delete the listing. Please try again.
      </p>
    );
  }, [hasError]);

  return (
    <AlertDialog isOpen={phone !== null} onOpenChange={(isOpen) => (isOpen ? undefined : close())}>
      <AlertDialog.Backdrop>
        <AlertDialog.Container>
          <AlertDialog.Dialog>
            <AlertDialog.Header>
              <AlertDialog.Icon status="danger" />
              <AlertDialog.Heading>Delete this listing?</AlertDialog.Heading>
            </AlertDialog.Header>
            <AlertDialog.Body className="flex flex-col gap-2">
              {phone ? <p className="font-medium">{phone.model_name}</p> : null}
              <p className="text-sm text-muted">The listing is removed from the search. This cannot be undone.</p>
              {deleteErrorJSX}
            </AlertDialog.Body>
            <AlertDialog.Footer>
              <Button variant="tertiary" onPress={close}>
                Cancel
              </Button>
              <Button variant="danger" onPress={() => void confirm()} isPending={isDeleting}>
                Delete listing
              </Button>
            </AlertDialog.Footer>
          </AlertDialog.Dialog>
        </AlertDialog.Container>
      </AlertDialog.Backdrop>
    </AlertDialog>
  );
}
