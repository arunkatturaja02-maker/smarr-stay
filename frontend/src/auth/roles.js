export const ROLE_DETAILS = {
  RECEPTIONIST: {
    label: 'Receptionist',
    shortLabel: 'Front desk',
    home: '/receptionist/dashboard',
    summary: 'Guest arrivals, departures, and room coordination.',
  },
  HOUSEKEEPING_MANAGER: {
    label: 'Housekeeping Manager',
    shortLabel: 'Operations',
    home: '/manager/dashboard',
    summary: 'Team priorities, assignment, and service oversight.',
  },
  HOUSEKEEPING_STAFF: {
    label: 'Housekeeping Staff',
    shortLabel: 'Service team',
    home: '/staff/dashboard',
    summary: 'Assigned rooms, service tasks, and completion updates.',
  },
}

export const REGISTRATION_ROLES = {
  receptionist: {
    role: 'RECEPTIONIST',
    path: '/register/receptionist',
    endpoint: '/api/auth/register/receptionist',
    label: 'Receptionist',
    eyebrow: 'Front desk registration',
    summary:
      'For team members who coordinate guest arrivals, departures, and room allocation.',
    highlights: ['Guest-facing coordination', 'Room allocation support'],
  },
  manager: {
    role: 'HOUSEKEEPING_MANAGER',
    path: '/register/manager',
    endpoint: '/api/auth/register/manager',
    label: 'Housekeeping Manager',
    eyebrow: 'Manager registration',
    summary:
      'For housekeeping leaders who will oversee priorities, assignments, and inspections.',
    highlights: ['Priority oversight', 'Team and inspection management'],
  },
  staff: {
    role: 'HOUSEKEEPING_STAFF',
    path: '/register/staff',
    endpoint: '/api/auth/register/staff',
    label: 'Housekeeping Staff',
    eyebrow: 'Service team registration',
    summary:
      'For housekeeping team members who complete room and service tasks.',
    highlights: ['Assigned task updates', 'Room readiness updates'],
  },
}

export function getRoleHome(role) {
  return ROLE_DETAILS[role]?.home || '/unauthorized'
}

export function getRoleLabel(role) {
  return ROLE_DETAILS[role]?.label || 'Staff member'
}
