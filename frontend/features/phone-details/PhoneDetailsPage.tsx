import { OS_LABELS } from "@/config/phone";
import { ConditionBadge } from "@/ui/molecules/ConditionBadge";
import { PageContainer } from "@/ui/layouts/PageContainer";
import { SpecList } from "@/ui/molecules/SpecList";
import { formatPriceUsd } from "@/utils/format";
import { buildPhoneSpecs } from "@/utils/phoneSpecs";
import { DealButton } from "./DealButton";
import { buildPhoneJsonLd, serializeJsonLd } from "./seo";

interface PhoneDetailsPageProps {
  phone: Entity.Phone;
}

/** Phone details page content: docs/features/PHONE_DETAILS.md#page-content. */
export function PhoneDetailsPage({ phone }: PhoneDetailsPageProps) {
  const specs = [
    { label: "Model", value: phone.model_name },
    { label: "OS", value: OS_LABELS[phone.os] },
    ...buildPhoneSpecs(phone),
  ];
  const conditionNote = phone.condition_note.trim();
  const conditionNoteJSX = conditionNote ? (
    <section aria-labelledby="phone-condition-note-heading" className="flex flex-col gap-3">
      <h2 id="phone-condition-note-heading" className="text-lg font-semibold">
        Seller&apos;s note on the condition
      </h2>
      <p className="leading-relaxed whitespace-pre-line text-muted">{conditionNote}</p>
    </section>
  ) : null;

  return (
    <PageContainer>
      <meta property="og:type" content="product" />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: serializeJsonLd(buildPhoneJsonLd(phone)) }}
      />
      <article className="flex flex-col gap-8">
        <header className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex flex-col gap-3">
            <h1 className="text-3xl font-semibold tracking-tight">{phone.model_name}</h1>
            <div className="flex flex-wrap items-center gap-3">
              <span className="text-muted">{OS_LABELS[phone.os]}</span>
              <ConditionBadge condition={phone.condition} />
            </div>
          </div>
          <div className="flex flex-col gap-3 sm:items-end">
            <p className="text-3xl font-semibold whitespace-nowrap">{formatPriceUsd(phone.price)}</p>
            <DealButton phoneId={phone.id} />
          </div>
        </header>

        <section aria-labelledby="phone-specs-heading" className="flex flex-col gap-3">
          <h2 id="phone-specs-heading" className="text-lg font-semibold">
            Specifications
          </h2>
          <SpecList
            specs={specs}
            className="grid-cols-2 gap-4 rounded-2xl border border-border bg-surface p-4 sm:grid-cols-5"
          />
        </section>

        <section aria-labelledby="phone-description-heading" className="flex flex-col gap-3">
          <h2 id="phone-description-heading" className="text-lg font-semibold">
            Description
          </h2>
          <p className="leading-relaxed whitespace-pre-line">{phone.description}</p>
        </section>

        {conditionNoteJSX}
      </article>
    </PageContainer>
  );
}
