PLATFORM VERSION INFO
	Windows 			: 10.0.26100.0 (Win32NT)
	Common Language Runtime 	: 4.0.30319.42000
	System.Deployment.dll 		: 4.8.9181.0 built by: NET481REL1LAST_C
	clr.dll 			: 4.8.9310.0 built by: NET481REL1LAST_C
	dfdll.dll 			: 4.8.9181.0 built by: NET481REL1LAST_C
	dfshim.dll 			: 10.0.26100.1882 (WinBuild.160101.0800)

SOURCES
	Deployment url			: file:///D:/Documents-D/VS%20Code/network%20programming/buoi3/AuthenticatedStreamClassApp/WinFormsHost/bin/Release/net8.0-windows/win-x64/publish/WinFormsHost.application

ERROR SUMMARY
	Below is a summary of the errors, details of these errors are listed later in the log.
	* Activation of D:\Documents-D\VS Code\network programming\buoi3\AuthenticatedStreamClassApp\WinFormsHost\bin\Release\net8.0-windows\win-x64\publish\WinFormsHost.application resulted in exception. Following failure messages were detected:
		+ Exception reading manifest from file:///D:/Documents-D/VS%20Code/network%20programming/buoi3/AuthenticatedStreamClassApp/WinFormsHost/bin/Release/net8.0-windows/win-x64/publish/WinFormsHost.application: the manifest may not be valid or the file could not be opened.
		+ Deployment manifest is not semantically valid.
		+ Application reference identity processor architecture, amd64, does not match the processor architecture of the deployment: msil.

COMPONENT STORE TRANSACTION FAILURE SUMMARY
	No transaction error was detected.

WARNINGS
	There were no warnings during this operation.

OPERATION PROGRESS STATUS
	* [11/10/2025 11:11:29 CH] : Activation of D:\Documents-D\VS Code\network programming\buoi3\AuthenticatedStreamClassApp\WinFormsHost\bin\Release\net8.0-windows\win-x64\publish\WinFormsHost.application has started.

ERROR DETAILS
	Following errors were detected during this operation.
	* [11/10/2025 11:11:29 CH] System.Deployment.Application.InvalidDeploymentException (ManifestParse)
		- Exception reading manifest from file:///D:/Documents-D/VS%20Code/network%20programming/buoi3/AuthenticatedStreamClassApp/WinFormsHost/bin/Release/net8.0-windows/win-x64/publish/WinFormsHost.application: the manifest may not be valid or the file could not be opened.
		- Source: System.Deployment
		- Stack trace:
			at System.Deployment.Application.ManifestReader.FromDocument(String localPath, ManifestType manifestType, Uri sourceUri)
			at System.Deployment.Application.DownloadManager.DownloadDeploymentManifestDirectBypass(SubscriptionStore subStore, Uri& sourceUri, TempFile& tempFile, SubscriptionState& subState, IDownloadNotification notification, DownloadOptions options, ServerInformation& serverInformation)
			at System.Deployment.Application.DownloadManager.DownloadDeploymentManifestBypass(SubscriptionStore subStore, Uri& sourceUri, TempFile& tempFile, SubscriptionState& subState, IDownloadNotification notification, DownloadOptions options)
			at System.Deployment.Application.ApplicationActivator.PerformDeploymentActivation(Uri activationUri, Boolean isShortcut, String textualSubId, String deploymentProviderUrlFromExtension, BrowserSettings browserSettings, String& errorPageUrl, Uri& deploymentUri)
			at System.Deployment.Application.ApplicationActivator.PerformDeploymentActivationWithRetry(Uri activationUri, Boolean isShortcut, String textualSubId, String deploymentProviderUrlFromExtension, BrowserSettings browserSettings, String& errorPageUrl)
--- End of stack trace from previous location where exception was thrown ---
			at System.Runtime.ExceptionServices.ExceptionDispatchInfo.Throw()
			at System.Deployment.Application.ApplicationActivator.PerformDeploymentActivationWithRetry(Uri activationUri, Boolean isShortcut, String textualSubId, String deploymentProviderUrlFromExtension, BrowserSettings browserSettings, String& errorPageUrl)
			at System.Deployment.Application.ApplicationActivator.ActivateDeploymentWorker(Object state)
		--- Inner Exception ---
		System.Deployment.Application.InvalidDeploymentException (ManifestSemanticValidation)
		- Deployment manifest is not semantically valid.
		- Source: System.Deployment
		- Stack trace:
			at System.Deployment.Application.Manifest.AssemblyManifest.ValidateSemanticsForDeploymentRole()
			at System.Deployment.Application.ManifestReader.FromDocument(String localPath, ManifestType manifestType, Uri sourceUri)
		--- Inner Exception ---
		System.Deployment.Application.InvalidDeploymentException (ManifestComponentSemanticValidation)
		- Application reference identity processor architecture, amd64, does not match the processor architecture of the deployment: msil.
		- Source: System.Deployment
		- Stack trace:
			at System.Deployment.Application.Manifest.AssemblyManifest.ValidateApplicationDependency(DependentAssembly da)
			at System.Deployment.Application.Manifest.AssemblyManifest.ValidateSemanticsForDeploymentRole()

COMPONENT STORE TRANSACTION DETAILS
	No transaction information is available.

