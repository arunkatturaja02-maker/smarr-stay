import DashboardPlaceholder from '../../components/DashboardPlaceholder'

const cards = [
  {
    title: 'My assigned rooms',
    description:
      'See the rooms and service tasks assigned to you for the current shift.',
  },
  {
    title: 'Task status updates',
    description:
      'Mark work as started, blocked, or complete so the whole team stays aligned.',
  },
  {
    title: 'Inspection results',
    description:
      'Review inspection feedback and understand what needs to be corrected.',
  },
]

export default function StaffDashboard() {
  return (
    <DashboardPlaceholder
      cards={cards}
      note="Housekeeping staff tools for assigned rooms, task updates, and inspection feedback will arrive in later modules. Module 1 confirms your staff-only authentication and access."
    />
  )
}
