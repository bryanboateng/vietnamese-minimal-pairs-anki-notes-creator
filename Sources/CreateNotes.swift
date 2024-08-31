import Algorithms
import ArgumentParser
import Foundation

struct MinimalPairComponent {
	let distinctiveFeature: String
	let word: String
}

struct TTSResponse: Decodable {
	let async: URL
	let error: Int
	let message, requestID: String

	enum CodingKeys: String, CodingKey {
		case async, error, message
		case requestID = "request_id"
	}
}

@main
struct CreateNotes: AsyncParsableCommand {
	@Argument(completion: .file(), transform: URL.init(fileURLWithPath:))
	var minimalPairComponentsFile: URL

	@Argument()
	var apiKey: String

	@Argument(completion: .directory, transform: URL.init(fileURLWithPath:))
	var mediaDirectory: URL

	func downloadMissingAudioFiles(
		minimalPairComponents: [MinimalPairComponent],
		exportDirectory: URL
	) async throws {
		let jsonDecoder = JSONDecoder()
		var ttsReponses = [(String, TTSResponse)]()
		for minimalPairComponent in minimalPairComponents {
			let filename = "tts-\(minimalPairComponent.word).wav"
			let audioExists = FileManager.default.fileExists(
				atPath: self.mediaDirectory
					.appending(component: filename)
					.path()
			)
			if !audioExists {
				var request = URLRequest(url: URL(string: "https://api.fpt.ai/hmi/tts/v5")!)
				request.httpMethod = "POST"
				request.setValue(self.apiKey, forHTTPHeaderField: "api-key")
				request.setValue("0.5", forHTTPHeaderField: "speed")
				request.setValue("banmai", forHTTPHeaderField: "voice")
				request.setValue("wav", forHTTPHeaderField: "format")

				let (responseData, response) = try await URLSession.shared.upload(
					for: request,
					from: Data(minimalPairComponent.word.utf8)
				)
				guard let httpResponse = response as? HTTPURLResponse,
						(200...299).contains(httpResponse.statusCode) else {
					print("Error getting \"\(minimalPairComponent.word)\"")
					continue
				}
				ttsReponses.append(
					(
						filename,
						try jsonDecoder.decode(TTSResponse.self, from: responseData)
					)
				)
			}
		}


		for (filename, ttsResponse) in ttsReponses {
			try await Task.sleep(for: .seconds(5))
			let (localURL, response2) = try await URLSession.shared.download(from: ttsResponse.async)
			guard let httpResponse = response2 as? HTTPURLResponse,
					(200...299).contains(httpResponse.statusCode) else {
				print("Error getting \(filename)")
				continue
			}
			print(localURL)
			try FileManager.default.moveItem(at: localURL, to: exportDirectory.appending(component: filename))
		}
	}
	func exportCSVFile(
		minimalPairComponents: [MinimalPairComponent],
		exportDirectory: URL
	) throws {
		let csvContent = minimalPairComponents
			.combinations(ofCount: 2)
			.reduce("") { partialResult, minimalPair in
				partialResult + "\n\(minimalPair[0].distinctiveFeature);\(minimalPair[0].word);\(minimalPair[1].distinctiveFeature);\(minimalPair[1].word)"
			}
			.trimmingCharacters(in: .whitespacesAndNewlines)

		try Data(csvContent.utf8)
			.write(to: exportDirectory.appending(path: "notes").appendingPathExtension("csv"))
	}

	mutating func run() async throws {
		let minimalPairComponents = try String(contentsOf: self.minimalPairComponentsFile)
			.trimmingCharacters(in: .whitespacesAndNewlines)
			.split(separator: "\n")
			.map { line in
				let trimmedLine = line
					.trimmingCharacters(in: .whitespacesAndNewlines)
					.split(separator: "|")
				return MinimalPairComponent(
					distinctiveFeature: trimmedLine[0].trimmingCharacters(in: .whitespaces).lowercased(),
					word: trimmedLine[1].trimmingCharacters(in: .whitespaces).lowercased()
				)
			}
			.sorted { $0.word < $1.word }

		let dateFormatter = DateFormatter()
		dateFormatter.dateFormat = "YY-MM-dd-HH-mm-ss"

		let exportDirectory = URL.desktopDirectory
			.appending(component: "vietnamese-minimal-pairs", directoryHint: .isDirectory)
			.appending(component: dateFormatter.string(from: .now), directoryHint: .isDirectory)
		try FileManager.default.createDirectory(at: exportDirectory, withIntermediateDirectories: true)
		try await downloadMissingAudioFiles(
			minimalPairComponents: minimalPairComponents,
			exportDirectory: exportDirectory
		)
		try exportCSVFile(
			minimalPairComponents: minimalPairComponents,
			exportDirectory: exportDirectory
		)
	}
}

