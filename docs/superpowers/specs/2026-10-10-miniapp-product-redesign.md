# TTStars Mini App product redesign

## Direction

TTStars uses a Telegram-native premium visual language: cold graphite surfaces,
one blue action accent, restrained borders, strong financial typography, and a
single coherent outline icon family. Product discovery may be more expressive,
but checkout, selling, history, and administration remain deliberately calm and
precise.

## Information architecture

- Home gives balanced access to Stars, Premium, Gifts, and selling Stars. Stars
  receive slightly more space because they are the most common purchase, not a
  different visual identity.
- Balance and the latest operation are secondary context, not the hero.
- Promotions appear only when backed by real product data. Evergreen product
  guidance must not be presented as a discount.
- Root destinations have no back action. A back action appears only inside a
  nested task and returns to the previous logical stage.
- Purchase and gift flows use descriptive screen titles instead of isolated
  numeric step counters.

## Responsive layout

- Mobile keeps focused, single-column tasks and a four-item bottom navigation.
- Desktop uses the available width as a workspace: product selection and input
  on the left, order summary or account context on the right.
- Commerce forms do not become stretched mobile cards. Their content and summary
  occupy distinct columns at desktop widths.

## Financial presentation

- Stars quantities use large, semibold tabular numerals.
- Quotes from the backend are the source of truth for base price, percentage and
  fixed fees, and checkout total.
- Selling Stars uses exchange/payout semantics, never sale/discount semantics.
- Pending, error, and completed states are visually and verbally distinct. A
  failed create request never claims that payment succeeded.

## Gifts

- Gift selection, recipient details, and payment remain separate phases.
- The catalog does not show a back action. Nested phases do.
- Payment repeats the selected gift, recipient, fee description, fee amount, and
  final total before the irreversible action.
- API failures are mapped to safe, actionable messages; provider details remain
  available for server diagnostics without exposing raw errors to users.

## Quality gates

- Existing API routes, financial rules, callback contracts, and data models stay
  unchanged unless a diagnosed backend defect requires a compatible fix.
- New behavior is introduced through failing tests first.
- Validate at 375, 768, 1024, and 1440 CSS pixels; preserve keyboard focus,
  44-pixel touch targets, reduced motion, and safe-area behavior.
