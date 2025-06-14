import * as React from 'react'
import { Outlet, createRootRoute } from '@tanstack/react-router'
import AppSidebar from '@/features/AppSidebar'
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar'

export const Route = createRootRoute({
    component: RootComponent,
})

function RootComponent() {
    return (
        <React.Fragment>
            <SidebarProvider>
                <AppSidebar />
                <SidebarInset>
                    <div className='p-8'>
                        <Outlet />
                    </div>
                </SidebarInset>
            </SidebarProvider>
        </React.Fragment>
    )
}
