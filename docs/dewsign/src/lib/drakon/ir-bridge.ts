// src/lib/drakon/ir-bridge.ts
import type { DrakonDiagram, DrakonItem } from '@/types/drakonwidget';
import type { DrakonSchemaIR, DrakonNodeIR, DrakonNodeType } from '@/types/drakon';

/**
 * Maps DRAKON-IR primitive node types to DrakonWidget internal element types.
 */
export function mapIrTypeToWidgetType(irType: DrakonNodeType): string {
  switch (irType) {
    case 'headline':
    case 'header':
      return 'header';
    case 'branch':
      return 'branch';
    case 'question':
      return 'question';
    case 'silhouette_route':
    case 'address':
      return 'address';
    case 'choice':
    case 'select':
      return 'select';
    case 'loopbegin':
      return 'loopbegin';
    case 'loopend':
      return 'loopend';
    case 'insertion':
      return 'insertion';
    case 'end':
      return 'end';
    case 'action':
    default:
      return 'action';
  }
}

/**
 * Converts canonical DRAKON-IR schema into DrakonWidget runtime format (DrakonDiagram).
 */
export function convertIrToDrakonDiagram(schema: DrakonSchemaIR): DrakonDiagram {
  const items: Record<string, DrakonItem> = {};

  for (const node of schema.nodes) {
    const itemType = mapIrTypeToWidgetType(node.node_type);

    const item: DrakonItem = {
      type: itemType,
      content: node.label,
      one: node.edges.down ?? undefined,
      two: node.edges.right ?? undefined,
      branchId: node.branch_id,
    };

    // Embed semantic binding info in secondary text or link for tooltip/inspection
    if (node.semantic_binding?.adr_invariant_id) {
      item.secondary = `[${node.semantic_binding.adr_invariant_id}]`;
    }

    items[node.node_id] = item;
  }

  return {
    name: schema.name,
    access: 'read',
    params: schema.params,
    items,
  };
}

/**
 * Converts DrakonWidget diagram format back into canonical DRAKON-IR.
 */
export function convertDrakonDiagramToIr(
  diagram: DrakonDiagram,
  bindingsMap: Record<string, DrakonNodeIR['semantic_binding']> = {}
): DrakonSchemaIR {
  const nodes: DrakonNodeIR[] = [];

  for (const [id, item] of Object.entries(diagram.items)) {
    let nodeType: DrakonNodeType = 'action';
    if (item.type === 'header') nodeType = 'headline';
    else if (item.type === 'branch') nodeType = 'branch';
    else if (item.type === 'question') nodeType = 'question';
    else if (item.type === 'end') nodeType = 'end';
    else if (item.type === 'address') nodeType = 'silhouette_route';

    nodes.push({
      node_id: id,
      node_type: nodeType,
      label: item.content || '',
      edges: {
        down: item.one || null,
        right: item.two || null,
      },
      branch_id: item.branchId,
      semantic_binding: bindingsMap[id],
    });
  }

  return {
    schema_version: '1.0',
    name: diagram.name || 'Exported Drakon Schema',
    params: diagram.params,
    nodes,
  };
}
