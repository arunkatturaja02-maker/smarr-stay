import { Route, Routes } from 'react-router-dom'
import {
  ProtectedRoute,
  PublicOnlyRoute,
  RoleRoute,
  RootRedirect,
} from './auth/RouteGuards'
import LoginPage from './pages/LoginPage'
import NotFoundPage from './pages/NotFoundPage'
import PendingApprovalPage from './pages/PendingApprovalPage'
import RegisterHubPage from './pages/RegisterHubPage'
import RegisterPage from './pages/RegisterPage'
import UnauthorizedPage from './pages/UnauthorizedPage'
import ManagerDashboard from './pages/dashboards/ManagerDashboard'
import ReceptionistDashboard from './pages/dashboards/ReceptionistDashboard'
import StaffDashboard from './pages/dashboards/StaffDashboard'

function App() {
  return (
    <Routes>
      <Route path="/" element={<RootRedirect />} />

      <Route element={<PublicOnlyRoute />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterHubPage />} />
        <Route
          path="/register/receptionist"
          element={<RegisterPage registrationKey="receptionist" />}
        />
        <Route
          path="/register/manager"
          element={<RegisterPage registrationKey="manager" />}
        />
        <Route
          path="/register/staff"
          element={<RegisterPage registrationKey="staff" />}
        />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route element={<RoleRoute allowedRoles={['RECEPTIONIST']} />}>
          <Route
            path="/receptionist/dashboard"
            element={<ReceptionistDashboard />}
          />
        </Route>

        <Route
          element={<RoleRoute allowedRoles={['HOUSEKEEPING_MANAGER']} />}
        >
          <Route path="/manager/dashboard" element={<ManagerDashboard />} />
        </Route>

        <Route element={<RoleRoute allowedRoles={['HOUSEKEEPING_STAFF']} />}>
          <Route path="/staff/dashboard" element={<StaffDashboard />} />
        </Route>
      </Route>

      <Route path="/pending-approval" element={<PendingApprovalPage />} />
      <Route path="/unauthorized" element={<UnauthorizedPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}

export default App
