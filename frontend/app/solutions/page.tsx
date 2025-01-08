import { Navigation } from '@/components/navigation'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

// This would typically come from your database
const solutionsData = {
  totalSolutions: 1000,
  yearDistribution: {
    2023: 300,
    2022: 250,
    2021: 200,
    // ... other years
  },
  toolTypes: {
    'Sequence Analysis': 200,
    'Structural Biology': 150,
    'Genomics': 300,
    // ... other tool types
  }
}

export default function Solutions() {
  return (
    <div className="flex flex-col min-h-screen">
      <Navigation />
      <main className="flex-grow container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">Biological Solutions Database</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Total Solutions</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-4xl font-bold">{solutionsData.totalSolutions}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Solutions by Year</CardTitle>
            </CardHeader>
            <CardContent>
              <ul>
                {Object.entries(solutionsData.yearDistribution).map(([year, count]) => (
                  <li key={year}>{year}: {count}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Solutions by Tool Type</CardTitle>
            </CardHeader>
            <CardContent>
              <ul>
                {Object.entries(solutionsData.toolTypes).map(([type, count]) => (
                  <li key={type}>{type}: {count}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}

