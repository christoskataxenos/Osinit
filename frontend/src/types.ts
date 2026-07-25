export interface IncidentSource {
  source_name: string;
  source_url: string;
  is_darknet?: boolean;
}

export interface Incident {
  id: string;
  title: string;
  description: string;
  summary?: string;
  severity?: 'Low' | 'Medium' | 'High' | 'Critical';
  tags?: string[];
  sources?: IncidentSource[];
  is_merged?: boolean;
  full_content?: string;
  source_name: string;
  source_url: string;
  is_darknet: boolean;
  date_reported: string;
}

export type FilterOption = 'all' | 'clearnet' | 'darknet';
export type TimeFilterOption = 'all' | '12h' | '24h';

export interface IsolatedContent {
  id: string;
  title: string;
  source_name: string;
  source_url: string;
  is_darknet: boolean;
  date_reported: string;
  sanitized_content: string;
  full_content: string;
  summary: string;
  entities: string[];
  reading_time_minutes: number;
  isolation_status: string;
  security_notice: string;
}
