export const defaultPlanId = "free"

export const pricingPlans = [
  {
    id: "free",
    name: "Free",
    description: "A free plan to get you started!",
    price: "$0",
    priceIntervalName: "per month",
    stripe_price_id: null,
    features: ["MIT Licence", "Fast Performance", "Stripe Integration"],
  },
  {
    id: "entrepreneur",
    name: "Entrepreneur",
    description: "A plan for entrepreneurs.",
    price: "$15",
    priceIntervalName: "per month",
    stripe_price_id: "price_1Py5hKFkRtr3A4QKamlEyFF6",
    stripe_product_id: "prod_QplDyyvWiq5qsB",
    features: [
      "Everything in Free",
      "Support us with fake money",
      "Test the purchase experience",
    ],
  },
  {
    id: "business",
    name: "Business",
    description: "A plan for businesses.",
    price: "$75",
    priceIntervalName: "per month",
    stripe_price_id: "price_1Py5hUFkRtr3A4QK0ELpOhLt",
    stripe_product_id: "prod_QplDGvsyk1Tx47",
    features: [
      "Everything in Pro",
      "Try the 'upgrade plan' UX",
      "Still actually free!",
    ],
  },
]
