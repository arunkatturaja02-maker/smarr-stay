import DashboardPlaceholder from '../../components/DashboardPlaceholder'

const cards = [
  {
    title: 'Housekeeping priority queue',
    description:
      'Review service priorities calculated from urgency and operational rules.',
  },
  {
    title: 'Staff assignment board',
    description:
      'Match housekeeping tasks to available staff while balancing workload.',
  },
  {
    title: 'Inspection tracking',
    description:
      'Record completed inspections and follow up on rooms that need attention.',
  },
]

export default function ManagerDashboard() {
  return (
    <DashboardPlaceholder
      cards={cards}
      note="Manager tools for priority queues, staff assignment, and inspections are planned for later modules. This Module 1 dashboard confirms your manager-only authentication and access."
    />
  )
}
