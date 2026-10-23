import DashboardPlaceholder from '../../components/DashboardPlaceholder'

const cards = [
  {
    title: 'Guest check-in & check-out',
    description:
      'Verify arrivals, confirm active stays, and support a smooth front-desk handover.',
  },
  {
    title: 'Smart room allocation',
    description:
      'Assign the right room using availability and housekeeping readiness signals.',
  },
  {
    title: 'Service request intake',
    description:
      'Record guest requests and pass them into the housekeeping priority workflow.',
  },
]

export default function ReceptionistDashboard() {
  return (
    <DashboardPlaceholder
      cards={cards}
      note="Receptionist tools such as guest check-in, room allocation, and service request intake will be implemented in later modules. Module 1 provides secure authentication and role enforcement only."
    />
  )
}
