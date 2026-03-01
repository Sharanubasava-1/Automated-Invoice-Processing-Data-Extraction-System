import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://azbquqmtktfyqndlqkwp.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6YnF1cW10a3RmeXFuZGxxa3dwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIzNDE4NTYsImV4cCI6MjA4NzkxNzg1Nn0.K8wpnixQGyRzq2NmThwOYm_itl2MXuyWMTwCqtgT0zY'

export const supabase = createClient(supabaseUrl, supabaseKey)