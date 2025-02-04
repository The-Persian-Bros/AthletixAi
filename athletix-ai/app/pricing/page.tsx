import { Check } from "lucide-react"
import { Button } from "../../components/ui/button"

const plans = [
  {
    name: "Basic",
    price: "$9",
    features: ["5 AI-powered analyses per month", "Basic performance tracking", "Email support"],
  },
  {
    name: "Pro",
    price: "$29",
    features: [
      "Unlimited AI-powered analyses",
      "Advanced performance tracking",
      "Priority support",
      "Custom AI coaching",
    ],
  },
  {
    name: "Enterprise",
    price: "Custom",
    features: ["Custom features", "Dedicated account manager", "On-premise deployment", "24/7 phone support"],
  },
]

export default function Pricing() {
  return (
    <section className="py-20">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-12 text-gradient">Choose Your Plan</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <div
              key={index}
              className="bg-background/80 backdrop-blur-lg p-8 rounded-lg shadow-lg border border-primary/20"
            >
              <h3 className="text-2xl font-bold mb-4">{plan.name}</h3>
              <p className="text-4xl font-bold mb-6 text-gradient">
                {plan.price}
                <span className="text-lg font-normal text-muted-foreground">/month</span>
              </p>
              <ul className="mb-8">
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-center mb-2">
                    <Check className="h-5 w-5 text-primary mr-2" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              <Button className="w-full hover-lift" variant={index === 1 ? "default" : "outline"}>
                {index === 2 ? "Contact Sales" : "Get Started"}
              </Button>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

