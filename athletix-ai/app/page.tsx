import Link from "next/link"
import { ArrowRight, Brain, Zap, BarChart, Video } from "lucide-react"
import { Button } from "../components/ui/button"
import Background from "../components/Background"
import MouseMoveEffect from "../components/MouseMoveEffect"

const features = [
    {
      name: "AI-Powered Analysis",
      description: "Get real-time insights on your performance using advanced machine learning algorithms.",
      icon: Brain,
    },
    {
      name: "Instant Feedback",
      description: "Receive immediate feedback on your form and technique to improve faster.",
      icon: Zap,
    },
    {
      name: "Progress Tracking",
      description: "Monitor your improvement over time with detailed performance metrics and visualizations.",
      icon: BarChart,
    },
    {
      name: "Video Analysis",
      description: "Upload or record videos for in-depth analysis of your movements and techniques.",
      icon: Video,
    },
  ]
  
  export default function Home() {
    return (
      <div className="relative min-h-screen">
        <Background />
        <MouseMoveEffect />
        <div className="relative z-10">
          <section className="container flex min-h-[calc(100vh-4rem)] max-w-screen-2xl flex-col items-center justify-center space-y-8 py-24 text-center md:py-32">
            <div className="space-y-4">
              <h1 className="bg-gradient-to-br from-foreground from-30% via-foreground/90 to-foreground/70 bg-clip-text text-4xl font-bold tracking-tight text-transparent sm:text-5xl md:text-6xl lg:text-7xl">
                Elevate Your Performance with
                <br />
                <span className="text-gradient">Athletix AI</span>
              </h1>
              <p className="mx-auto max-w-[42rem] leading-normal text-muted-foreground sm:text-xl sm:leading-8">
                Harness the power of AI to analyze your movements, receive real-time feedback, and take your athletic
                performance to the next level. 🏋️‍♂️🤖
              </p>
            </div>
            <div className="flex gap-4">
              <Button size="lg" asChild>
                <Link href="/dashboard">
                  Get Started
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link href="/pricing">View Pricing</Link>
              </Button>
            </div>
          </section>
  
          <section className="container space-y-16 py-24 md:py-32">
            <div className="mx-auto max-w-[58rem] text-center">
              <h2 className="font-bold text-3xl leading-[1.1] sm:text-3xl md:text-5xl">Cutting-Edge Features</h2>
              <p className="mt-4 text-muted-foreground sm:text-lg">
                Discover how Athletix AI can transform your training and performance.
              </p>
            </div>
            <div className="mx-auto grid max-w-5xl grid-cols-1 gap-8 md:grid-cols-2">
              {features.map((feature) => (
                <div
                  key={feature.name}
                  className="relative overflow-hidden rounded-lg border border-primary/20 bg-background/80 backdrop-blur-lg p-8 hover-lift"
                >
                  <div className="flex items-center gap-4">
                    <feature.icon className="h-8 w-8 text-primary" />
                    <h3 className="font-bold">{feature.name}</h3>
                  </div>
                  <p className="mt-2 text-muted-foreground">{feature.description}</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    )
  }
  