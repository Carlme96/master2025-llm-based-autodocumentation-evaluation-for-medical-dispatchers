import ReportPage from '@/features/ReportPage'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/$reportId')({
  component: RouteComponent,
})

function RouteComponent() {
  return <ReportPage />
}
