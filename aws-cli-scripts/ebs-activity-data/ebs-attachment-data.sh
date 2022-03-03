#!/bin/bash
printf "Region\tVolumeID\tVolumeName\tLastActivity\tVolumeURL\n" > volume_details.csv
for REGION in `aws ec2 describe-regions --output text | cut -f4`
do
    for VOLUME_ID in `aws ec2 describe-volumes --region $REGION --query "Volumes[*].{VolumeID:VolumeId}" --output text`
    do
        echo $REGION $VOLUME_ID
        attachment_state=$(aws ec2 describe-volumes --region $REGION --volume-ids $VOLUME_ID | jq -r .Volumes[].Attachments[].State)
        NAME=$(aws ec2 describe-volumes --volume-ids $VOLUME_ID --region $REGION --query "Volumes[*].{Name:Tags[?Key=='Name']|[0].Value}" --output text)
        if [ -z "${attachment_state}" ]; then
            instance_id=$(aws cloudtrail lookup-events --lookup-attributes AttributeKey=ResourceName,AttributeValue=$VOLUME_ID --max-results 1 --region $REGION --query 'Events[?EventName == `DetachVolume`].{EventTime:EventTime,InstanceID:(Resources[1].ResourceName)}' | jq -r .[].InstanceID)
            event_date=$(aws cloudtrail lookup-events --lookup-attributes AttributeKey=ResourceName,AttributeValue=$VOLUME_ID --max-results 1 --region $REGION --query 'Events[?EventName == `DetachVolume`].{EventTime:EventTime,InstanceID:(Resources[1].ResourceName)}' | jq -r .[].EventTime)
            if [ -z "${event_date}" ]; then
                last_activity=90
            else
                let last_activity=($(date +%s ) - $(date +%s -d $event_date ))/86400
            fi
            #build the volume link in format  https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#VolumeDetails:volumeId=vol-75933f0a
            VOLUME_URL=https://console.aws.amazon.com/ec2/v2/home?region=$REGION#VolumeDetails:volumeId=$VOLUME_ID
            if (( last_activity > 30 )); then
                printf "$REGION\t$VOLUME_ID\t$NAME\t$last_activity\t$VOLUME_URL\n" >> volume_details.csv
            fi
        fi
    done
done