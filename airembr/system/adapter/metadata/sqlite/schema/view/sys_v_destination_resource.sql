CREATE VIEW IF NOT EXISTS sys_v_destination_resource AS
SELECT id,
       'resource' AS resource_type,
       timestamp,
       name,
       description,
       type,
       tags,
       icon,
       credentials,
       destination,
       `groups`,
       enabled,
       locked,
       production,
       tenant
FROM sys_resource WHERE destination IS NOT NULL

UNION

SELECT id,
       'workflow' AS resource_type,
       timestamp AS deploy_timestamp,
       name,
       description,
       'workflow' as type,
       tags,
       'workflow' AS icon,
       NULL AS credentials,
       NULL AS destination,
       NULL AS `groups`,
       enabled,
       lock AS locked,
       production,
       tenant
FROM sys_workflow;