import { Navigation } from '@/components/navigation'
import { Button } from "@/components/ui/button"
import Image from 'next/image'

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navigation />
      <main className="flex-grow container mx-auto px-4 py-8">
        <section className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Welcome to BioinfoGPT</h1>
          <p className="text-xl mb-6">Your intelligent assistant for bioinformatics research</p>
          <Button asChild>
            <a href="/chat">Try BioinfoGPT Now</a>
          </Button>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Our Vision</h2>
          <p>BioinfoGPT aims to be an efficient and convenient research assistant in the field of bioinformatics, providing intelligent support for learning and analysis in medical bioinformatics research.</p>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">Key Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="border p-4 rounded-lg">
              <h3 className="text-xl font-semibold mb-2">Intelligent Tool Recommendations</h3>
              <p>Get personalized recommendations for bioinformatics software tools based on your research needs.</p>
            </div>
            <div className="border p-4 rounded-lg">
              <h3 className="text-xl font-semibold mb-2">Smart Documentation Q&A</h3>
              <p>Ask questions about tool usage and get instant, accurate answers from our intelligent system.</p>
            </div>
            <div className="border p-4 rounded-lg">
              <h3 className="text-xl font-semibold mb-2">Bioinformatics Database Queries</h3>
              <p>Effortlessly query and retrieve information from various bioinformatics databases.</p>
            </div>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4">About Us</h2>
          <p>BioinfoGPT is developed by a team of passionate bioinformaticians and AI researchers dedicated to advancing the field of bioinformatics through innovative technologies.</p>
        </section>
      </main>
      <footer className="bg-gray-100 py-4 text-center">
        <p>&copy; 2024 BioinfoGPT. All rights reserved.</p>
      </footer>
    </div>
  )
}

