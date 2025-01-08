import { Navigation } from '@/components/navigation'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

// This would typically come from your database
const toolsData = [
  {
    name: 'BLAST',
    input: 'DNA or protein sequence',
    description: 'Basic Local Alignment Search Tool for finding regions of similarity between biological sequences',
    output: 'Sequence alignments and similarity scores'
  },
  {
    name: 'HMMER',
    input: 'Protein sequence or multiple sequence alignment',
    description: 'Hidden Markov Model-based sequence analysis tool for protein sequence analysis',
    output: 'Profile HMMs, sequence alignments, and homology detection results'
  },
  // Add more tools as needed
]

export default function Tools() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navigation />
      <main className="flex-grow container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">Bioinformatics Tools</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {toolsData.map((tool, index) => (
            <Card key={index}>
              <CardHeader>
                <CardTitle>{tool.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <p><strong>Input:</strong> {tool.input}</p>
                <p><strong>Description:</strong> {tool.description}</p>
                <p><strong>Output:</strong> {tool.output}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  )
}

