# Follow pods feature specification

We want to introduce a feature that enables pod admins and/or users to follow all accessible **content** and **activities** on a remote pod.

### The issue

When a pod admin sets up a new pod the interface appears blank. This can make the app feel empty and confusing.

### The solution

We provide a way for users to explore content from accessible remote pods.

## Feature behavior

This feature enables admins (not users) to follow remote pods to display and interact with this pods's **public** activities. This includes:

- **Channel metadata**
- **Public library metadata**
- **Public Playlists**

This content appears on the requesting user's pod for their users to interact with.

### Backend

#### Following

1. To get public activities from remote domains, we will use the AP `Follow`. The service actor will be used to follow the remote service actor. Approval is automatic unless the admin has opt out of this feature (see #2542).
   note : about the service actor see https://socialhub.activitypub.rocks/t/fep-2677-identifying-the-application-actor/3646.

   - [x] Request : POST to `api/v2/federation/follows/domain` with `{"target": "pod_url"}`
   - [x] delete Request : POST to `api/v2/federation/follows/domain/delete` with `{"target": "pod_url"}`

2. We already have a variable used to route activities to the service actor (see`instances_with_followers`).

- [ ] make sure `followers` privacy level activities are only send once per pod

This need to be implemented for this public activities :

- [x] channel
- [x] upload
- [x] playlists
- [x] listenings
- [x] favorites

#### Fetching / scanning

With following we only receive new activities. We also want to fetch old ones to get content quickly. There might be a loooot of them and this might be heavy on the remote pod. So we can't blindly parse everything. That's why We will fetch in this priority **Music Channels**, **Playlists**, **Public Uploads**.

Fetching remote content is complex. Since we already have a fetching mechanism we will use it. We only need the objects URI. For performance reason will be nice to upgrade the Channels and Playlists endpoints to return only fid : `/channels/?fields=fid`. This could be apply to the serializers we want to :

```
class FilterFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = self.context["request"].query_params.get("fields")
        super().__init__(*args, **kwargs)

        if fields:
            allowed = set(fields.split(","))
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
```

Then each fid is used to create a async task for fetching.

- [x] We should create a variable that limits the number of objects to fetch. Already have `FEDERATION_COLLECTION_MAX_PAGES`.

For **public upload** this should be a fetch on public libraries : `/api/v2/libraries/`. This is not supported by the Fetch task. Might be fast to implement tho'. (update done in !3020)

### Frontend

- [ ] manage/moderation/domains : add an action to follow the pod
- [ ] manage/moderation/domains : add a follow filter
- [x] Provide a setting to disable Follow on the service actor (`Pod level following enabled`)

## Open questions

## Minimum viable product

The MVP for this feature is to implement the endpoint. We can ship this to users without breaking anything and test it with real data.

### Next steps

After the MVP we can build the **admin** access to the feature to assess how much strain the feature puts on a pod. If the feature works well enough we can give admins an option to give **all users** access to the feature.

- [ ] Automatic discovery and federation with pods (#2541)
- [ ] Deny-lists and opt out of automatic discovery (#2542)
- [ ] Support listening scan for pod follow
- [ ] Endpoint/command line to request a full scan of a pod ?
