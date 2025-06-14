import { Select, SelectItem, SelectContent, SelectTrigger, SelectValue } from "@/components/ui/select"
import { $api } from "@/fetchclient"
import { useMemo } from "react"


export default function AllReports() {

    const { data } = $api.useQuery("get", "/report/get_reports", {}, { refetchInterval: 10000 })


    const items = useMemo(() => {
        if (!data) return []
        return data.map((item) => (<SelectItem value={item.id} key={item.id}>{item.createdAt}</SelectItem>))
    }, [data])

    return (
        <Select>
            <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Report" />
            </SelectTrigger>
            <SelectContent>
                {items}
            </SelectContent>

        </Select>
    )
}