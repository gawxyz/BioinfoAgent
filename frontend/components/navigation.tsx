import Link from 'next/link'
import { Button } from "@/components/ui/button"

export function Navigation() {
  return (
    <nav className="bg-background/95 supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50 w-full border-b backdrop-blur">
      <div className="container flex h-14 items-center">
        <div className="mr-4 hidden md:flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <span className="hidden font-bold sm:inline-block">BioinfoGPT</span>
          </Link>
          <nav className="flex items-center space-x-6 text-sm font-medium">
            <Link href="/">Home</Link>
            <Link href="/chat">Chat</Link>
            <Link href="/solutions">Solutions</Link>
            <Link href="/docs">Docs</Link>
            <Link href="/tools">Tools</Link>
          </nav>
        </div>
      </div>
    </nav>
  )
}

