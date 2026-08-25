import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router'
import './index.css'
import { router } from './router.tsx'
import { AuthProvider } from './context/AuthContext.tsx'
import { Toaster } from './components/ui/toast.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Toaster>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </Toaster>
  </StrictMode>,
)
