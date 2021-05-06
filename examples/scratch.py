from balalaika.tracers import BasicTracer, MermaidSequenceDiagramTracer
import trio


trio.run(
    trio.open_tcp_stream, "github.com", 443,
    instruments=[MermaidSequenceDiagramTracer()],
)
