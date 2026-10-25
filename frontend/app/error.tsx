"use client";

import { Button } from "@heroui/react";
import { PageContainer } from "@/ui/layouts/PageContainer";
import { Alert } from "@/ui/molecules/Alert";

interface ErrorPageProps {
  error: unknown;
  retry: () => void;
}

/** Error boundary of all routes: docs/frontend/DESIGN.md#errors. */
export default function ErrorPage({ retry }: ErrorPageProps) {
  return (
    <PageContainer>
      <Alert
        title="Something went wrong. Please try again later."
        action={
          <Button size="sm" variant="secondary" onPress={() => retry()}>
            Try again
          </Button>
        }
      />
    </PageContainer>
  );
}
