
import { Button, buttonVariants } from "@/components/ui/button"
import { X, LoaderCircle, NotepadText, CircleSmall, Circle } from "lucide-react"
import {
    Sidebar,
    SidebarContent,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarRail,
} from "@/components/ui/sidebar"
import { $api } from "@/fetchclient"
import { Link } from "@tanstack/react-router"
import { useMemo } from "react"
import { ModeToggle } from "@/components/mode-toggle"

export default function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
    const { data } = $api.useQuery("get", "/report/get_reports")

    const items = useMemo(() => {
        if (!data) return []
        return data.map((report) => {
            return (<SidebarMenuItem key={report.id} className="list-none">
                <SidebarMenuButton asChild>
                    <Link to={report.id} from="/">
                        {<Circle />}
                        <span>{report.id}</span>
                    </Link>
                </SidebarMenuButton>
            </SidebarMenuItem>)
        })
    }, [data])


    return (<Sidebar>
        <div className="mt-4 flex gap-2 w-full justify-center">
            <ModeToggle />
            <Link to="/generate" className={`${buttonVariants({ variant: "outline" })}`}>Generate new report</Link>
        </div>
        <SidebarGroup>
            <SidebarGroupLabel>Reports</SidebarGroupLabel>
            <SidebarGroupContent>
                <SidebarMenu>
                    {items}
                </SidebarMenu>
            </SidebarGroupContent>
        </SidebarGroup>
    </Sidebar>)
}