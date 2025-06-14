import createFetchClient from "openapi-fetch";
import createClient from "openapi-react-query";
import type { paths } from "@/schema/schema"

export const fetchClient = createFetchClient<paths>({
    baseUrl: "http://localhost:8000/",
});
export const $api = createClient(fetchClient);