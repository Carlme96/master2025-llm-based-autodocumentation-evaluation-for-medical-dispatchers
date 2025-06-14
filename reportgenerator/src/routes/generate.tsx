import GenerateReport from '@/features/GenerateReport'
import { $api } from '@/fetchclient'
import { createFileRoute } from '@tanstack/react-router'
import { useMemo } from 'react'

export const Route = createFileRoute('/generate')({
  component: RouteComponent,
})

function RouteComponent() {
  const { data } = $api.useQuery("get", "/report/get-example-prompts")

  const formattedData = useMemo(() => {
    if (!data) return null
    return {

      props: {
        ...data.props,
        baseData: {
          ...data.props.baseData,
          transcription: JSON.stringify(data.props.baseData.transcription, null, 2),
        }
      },
      descriptions: {
        evaluateBotPromptDescriptions: data.evaluateBotPromptDescriptions,
        summaryBotPromptDescriptions: data.summaryBotPromptDescriptions,
      }


    }
  }, [data])

  if (!formattedData) return (<></>)

  return <GenerateReport examples={formattedData.props} descriptions={formattedData.descriptions} />
}
