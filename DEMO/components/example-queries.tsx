"use client"

import { Button } from "@/components/ui/button"
import { Lightbulb, Database, TrendingUp, AlertTriangle } from "lucide-react"

interface ExampleQueriesProps {
  onQuerySelect: (query: string) => void
}

const exampleQueries = [
  {
    icon: <Database className="h-4 w-4" />,
    title: "Análise de Uso",
    query: "Qual foi o tempo total de uso do motor (em horas) por chassi?",
    description: "Consulta sobre tempo de uso do motor por equipamento"
  },
  {
    icon: <TrendingUp className="h-4 w-4" />,
    title: "Eficiência por Cliente",
    query: "Qual cliente apresenta maior proporção de tempo improdutivo (marcha lenta) ou em baixo uso (carga baixa) em relação ao tempo total do motor?",
    description: "Análise de eficiência por cliente"
  },
  {
    icon: <Lightbulb className="h-4 w-4" />,
    title: "Categorias de Telemetria",
    query: "Qual a categoria de telemetria mais utilizada?",
    description: "Análise de categorias de dados de telemetria"
  },
  {
    icon: <AlertTriangle className="h-4 w-4" />,
    title: "Manutenção Preventiva",
    query: "É possível identificar equipamentos com manutenção preventiva necessária com base nos padrões de uso?",
    description: "Análise preditiva de manutenção"
  }
]

export function ExampleQueries({ onQuerySelect }: ExampleQueriesProps) {
  return (
    <div className="p-6">
      <h3 className="text-lg font-semibold mb-4 text-white">💡 Exemplos de Consultas</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {exampleQueries.map((example, index) => (
          <div
            key={index}
            className="bg-muted/20 border border-border rounded-lg p-4 hover:bg-muted/30 transition-colors cursor-pointer"
            onClick={() => onQuerySelect(example.query)}
          >
            <div className="flex items-center gap-2 mb-2">
              {example.icon}
              <h4 className="font-medium text-white">{example.title}</h4>
            </div>
            <p className="text-sm text-white/80 mb-3">{example.description}</p>
            <p className="text-xs text-white/60 line-clamp-2">{example.query}</p>
            <Button
              variant="ghost"
              size="sm"
              className="mt-3 text-primary hover:text-primary/80"
              onClick={(e) => {
                e.stopPropagation()
                onQuerySelect(example.query)
              }}
            >
              Usar este exemplo
            </Button>
          </div>
        ))}
      </div>
    </div>
  )
} 