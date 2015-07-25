#!/bin/bash

STAGE=$1
SCRIPT_HOME=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
TAG=
GIT=$(which git)

incrementVersionLastElement()
{
	OLDVERSION=$1
	VER1=$(echo "$OLDVERSION" | awk -F\. 'BEGIN{i=2}{res=$1; while(i<NF){res=res"."$i; i++}print res}')
	VER2=$(echo "$OLDVERSION" | awk -F\. '{print $NF}')
	let VER2=$VER2+1
	NEWVERSION="$VER1.$VER2"
	echo -n $NEWVERSION
}

# Set new release version
setNewVersion()
{
	#if [[ "$GIT_BRANCH" =~ (^(origin)/(feature)/(tagging)+$) ]]
	if [[ "$GIT_BRANCH" =~ (^(origin)/(master)+$) ]]
	then
		TAG=`head -1 "${WORKSPACE}/version.txt"`
		if [ ! -z $TAG ]
		then
			TAG=$(incrementVersionLastElement $TAG)
			echo $TAG > "${WORKSPACE}/version.txt"

			
		else
			abort "Setting new version failed"
		fi
	fi
}

# Push new version to Stash
pushNewVersion()
{
	#if [[ "$GIT_BRANCH" =~ (^(origin)/(feature)/(tagging)+$) ]]
	if [[ "$GIT_BRANCH" =~ (^(origin)/(master)+$) ]]
	then
		TAG=`head -1 "${WORKSPACE}/version.txt"`

		logger "Commit new version $TAG" 
		$GIT commit -a -m "Set new version $TAG" || return 1

		logger "Tag new version $TAG"
		$GIT tag "$TAG" || return 1

		GIT_SHORT_BRANCH=$(echo -n ${GIT_BRANCH} | sed 's,origin/,,g')

		logger "Push new version"
		$GIT push origin HEAD:$GIT_SHORT_BRANCH || return 1

		logger "Git push tags [$TAG]"
		$GIT push --tags origin HEAD:$GIT_SHORT_BRANCH || return 1
	fi
}


########
# MAIN #
########

# Create GIT tag
setNewVersion || exit 1
# Deploy and push the GIT tag
$SCRIPT_HOME/deployPack.sh && pushNewVersion || exit 1

