//! CLI adapter for article image attribution.

use silan_viking_app::{
    ArticleImageAttributionWorkspace, ImageAttributionApplyState, ImageWatermarkMode,
    ImageWatermarkPosition,
};
use std::path::Path;

pub fn watermark(content_root: &Path, target_uri: &str, args: &[&str]) -> Result<(), String> {
    let options = WatermarkOptions::parse(args)?;
    let workspace =
        ArticleImageAttributionWorkspace::open(content_root).map_err(|error| error.to_string())?;
    if options.dry_run {
        let plan = workspace
            .plan(target_uri, options.mode, options.position)
            .map_err(|error| error.to_string())?;
        if options.json {
            println!(
                "{}",
                serde_json::to_string_pretty(&plan).map_err(|error| error.to_string())?
            );
        } else {
            print_plan(&plan);
        }
        return Ok(());
    }

    let result = workspace
        .apply(target_uri, options.mode, options.position)
        .map_err(|error| error.to_string())?;
    if options.json {
        println!(
            "{}",
            serde_json::to_string_pretty(&result).map_err(|error| error.to_string())?
        );
    } else {
        print_plan(&result.plan);
        for asset in result.assets {
            let state = match asset.state {
                ImageAttributionApplyState::Applied => "applied",
                ImageAttributionApplyState::Unchanged => "unchanged",
                ImageAttributionApplyState::SkippedUnsupported => "skipped-unsupported",
            };
            println!("{state}\t{}\t{} bytes", asset.uri, asset.byte_count);
        }
    }
    Ok(())
}

pub fn inspect(content_root: &Path, asset_uri: &str, args: &[&str]) -> Result<(), String> {
    let json = match args {
        [] => false,
        ["--json"] => true,
        [other, ..] => return Err(format!("unknown media inspect flag `{other}`")),
    };
    let workspace =
        ArticleImageAttributionWorkspace::open(content_root).map_err(|error| error.to_string())?;
    let attribution = workspace
        .inspect_asset(asset_uri)
        .map_err(|error| error.to_string())?;
    if json {
        println!(
            "{}",
            serde_json::to_string_pretty(&attribution).map_err(|error| error.to_string())?
        );
    } else if let Some(attribution) = attribution {
        println!("attributed=true");
        println!("project={}", attribution.title);
        println!("venue={}", attribution.publication_venue);
        println!("author={}", attribution.author);
        println!("site={}", attribution.site_url);
        println!("article={}", attribution.article_url);
        println!("project_url={}", attribution.project_url);
        println!("fingerprint={}", attribution.fingerprint);
    } else {
        println!("attributed=false");
    }
    Ok(())
}

fn print_plan(plan: &silan_viking_app::ArticleImageAttributionPlan) {
    println!("target={}", plan.target_uri);
    println!(
        "policy={:?} position={:?} assets={}",
        plan.mode,
        plan.position,
        plan.assets.len()
    );
    for line in &plan.visible_lines {
        println!("preview={line}");
    }
}

#[derive(Default)]
struct WatermarkOptions {
    mode: Option<ImageWatermarkMode>,
    position: Option<ImageWatermarkPosition>,
    dry_run: bool,
    json: bool,
}

impl WatermarkOptions {
    fn parse(args: &[&str]) -> Result<Self, String> {
        let mut options = Self::default();
        let mut index = 0;
        while index < args.len() {
            match args[index] {
                "--mode" => {
                    index += 1;
                    options.mode = Some(
                        ImageWatermarkMode::parse(
                            args.get(index)
                                .ok_or("media watermark --mode requires a value")?,
                        )
                        .map_err(|error| error.to_string())?,
                    );
                }
                value if value.starts_with("--mode=") => {
                    options.mode = Some(
                        ImageWatermarkMode::parse(value.trim_start_matches("--mode="))
                            .map_err(|error| error.to_string())?,
                    );
                }
                "--position" => {
                    index += 1;
                    options.position = Some(
                        ImageWatermarkPosition::parse(
                            args.get(index)
                                .ok_or("media watermark --position requires a value")?,
                        )
                        .map_err(|error| error.to_string())?,
                    );
                }
                value if value.starts_with("--position=") => {
                    options.position = Some(
                        ImageWatermarkPosition::parse(value.trim_start_matches("--position="))
                            .map_err(|error| error.to_string())?,
                    );
                }
                "--dry-run" => options.dry_run = true,
                "--json" => options.json = true,
                value => return Err(format!("unknown media watermark flag `{value}`")),
            }
            index += 1;
        }
        Ok(options)
    }
}
