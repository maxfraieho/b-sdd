// src/types/specs.ts

export interface TaskItem {
  id: string;
  title: string;
  completed: boolean;
  raw_line?: string;
}

export interface SpecItem {
  id: string;
  title: string;
  path: string;
  tasks: TaskItem[];
  tasks_count: number;
  completed_count: number;
  percent: number;
  has_diagram: boolean;
  diagrams: string[];
  spec_markdown?: string;
  plan_markdown?: string;
}

export interface SpecsResponse {
  total: number;
  specs: SpecItem[];
}

export interface ProjectInfo {
  id: string;
  name: string;
  path: string;
  branch: string;
  commit: string;
  dirty_files: number;
  description: string;
  stats: {
    specs: number;
    adrs: number;
    tests: number;
    utopia_kb: string;
  };
}

export interface ProjectsResponse {
  current_project: ProjectInfo;
  workspaces: Array<{
    id: string;
    name: string;
    path: string;
    active: boolean;
  }>;
}
