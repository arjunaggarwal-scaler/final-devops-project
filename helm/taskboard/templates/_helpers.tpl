{{- define "taskboard.fullname" -}}{{ .Release.Name }}-taskboard{{- end }}
{{- define "taskboard.namespace" -}}{{ .Values.namespace }}{{- end }}
