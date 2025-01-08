import { Navigation } from '@/components/navigation'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

// This would typically come from your database
const docsData = {
  totalDocs: 500,
  sourceDistribution: {
    'Official Documentation': 200,
    'Research Papers': 150,
    'Tutorials': 100,
    'User Guides': 50
  }
}

export default function Docs() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navigation />
      <main className="flex-grow container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">Reference Documentation</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Total Documents</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-4xl font-bold">{docsData.totalDocs}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Documents by Source</CardTitle>
            </CardHeader>
            <CardContent>
              <ul>
                {Object.entries(docsData.sourceDistribution).map(([source, count]) => (
                  <li key={source}>{source}: {count}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}

