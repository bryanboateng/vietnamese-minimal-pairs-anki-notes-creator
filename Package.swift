// swift-tools-version: 5.10
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
	name: "VietnameseMinimalPairsAnkiCardCreator",
	platforms: [.macOS(.v13)],
	dependencies: [
		.package(url: "https://github.com/apple/swift-algorithms", from: "1.2.0"),
		.package(url: "https://github.com/apple/swift-argument-parser", from: "1.3.0"),
	],
	targets: [
		.executableTarget(
			name: "VietnameseMinimalPairsAnkiCardCreator",
			dependencies: [
				.product(name: "Algorithms", package: "swift-algorithms"),
				.product(name: "ArgumentParser", package: "swift-argument-parser"),
			]
		),
	]
)
